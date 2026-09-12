"""PCAP/CSV traffic ingestion into normalized five-second network state vectors."""
import io
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

FEATURE_NAMES = ["packet_count", "byte_count", "flow_count", "syn_count", "ack_count", "rst_count", "ttl_mean", "ttl_variance", "window_mean", "payload_mean", "payload_std", "iat_mean", "iat_variance", "port_445_count"]

def _normalise(frame):
    frame = frame.reindex(columns=FEATURE_NAMES, fill_value=0).replace([np.inf, -np.inf], 0).fillna(0)
    if len(frame) < 2: return frame.to_numpy(dtype=np.float32)
    return StandardScaler().fit_transform(frame).astype(np.float32)

def extract_csv(raw: bytes):
    df = pd.read_csv(io.BytesIO(raw))
    lower = {str(c).lower(): c for c in df.columns}
    def col(*names, default=0):
        for name in names:
            if name in lower: return pd.to_numeric(df[lower[name]], errors="coerce").fillna(default)
        return pd.Series(default, index=df.index)
    # Keep the fallback as a Series. Pandas ``fillna`` only accepts scalars,
    # mappings, or Series—not a raw ndarray.
    timestamp_column = next((lower[name] for name in ("timestamp", "time") if name in lower), None)
    timestamps = (pd.to_numeric(df[timestamp_column], errors="coerce") if timestamp_column else pd.Series(np.arange(len(df)), index=df.index, dtype=float))
    timestamps = timestamps.fillna(pd.Series(np.arange(len(df)), index=df.index, dtype=float))
    seconds = pd.to_datetime(timestamps, errors="coerce", unit="s")
    if seconds.isna().all(): groups = pd.Series(np.arange(len(df)) // 20)
    else: groups = seconds.dt.floor("5s")
    work = pd.DataFrame({"bytes": col("tot len fwd pkts", "packet length", "flow bytes/s"), "packets": col("total forward packets", "total packets", "packets"), "syn": col("syn flag count"), "ack": col("ack flag count"), "rst": col("rst flag count"), "ttl": col("ttl"), "window": col("init_win_bytes_forward", "tcp window size"), "payload": col("payload size", "packet length"), "iat": col("flow iat mean", "iat"), "port": col("destination port", "dst port")})
    agg = work.groupby(groups).agg(packet_count=("packets", "count"), byte_count=("bytes", "sum"), flow_count=("packets", "count"), syn_count=("syn", "sum"), ack_count=("ack", "sum"), rst_count=("rst", "sum"), ttl_mean=("ttl", "mean"), ttl_variance=("ttl", "var"), window_mean=("window", "mean"), payload_mean=("payload", "mean"), payload_std=("payload", "std"), iat_mean=("iat", "mean"), iat_variance=("iat", "var"), port_445_count=("port", lambda x: (x == 445).sum()))
    return _normalise(agg), list(map(str, agg.index))

def extract_pcap(raw: bytes):
    from scapy.all import IP, TCP, rdpcap
    packets = rdpcap(io.BytesIO(raw))
    rows = []
    for p in packets:
        if IP not in p: continue
        tcp = p[TCP] if TCP in p else None; flags = int(tcp.flags) if tcp else 0
        rows.append({"bucket": int(float(p.time)//5), "bytes": len(p), "syn": int(bool(flags & 2)), "ack": int(bool(flags & 16)), "rst": int(bool(flags & 4)), "ttl": p[IP].ttl, "window": tcp.window if tcp else 0, "payload": len(tcp.payload) if tcp else 0, "port445": int(bool(tcp and (tcp.sport == 445 or tcp.dport == 445)) )})
    if not rows: raise ValueError("No IP packets found in PCAP")
    df = pd.DataFrame(rows); agg = df.groupby("bucket").agg(packet_count=("bytes", "count"), byte_count=("bytes", "sum"), flow_count=("bytes", "count"), syn_count=("syn", "sum"), ack_count=("ack", "sum"), rst_count=("rst", "sum"), ttl_mean=("ttl", "mean"), ttl_variance=("ttl", "var"), window_mean=("window", "mean"), payload_mean=("payload", "mean"), payload_std=("payload", "std"), iat_mean=("bytes", "count"), iat_variance=("bytes", "var"), port_445_count=("port445", "sum"))
    return _normalise(agg), [str(k * 5) for k in agg.index]

def extract_features(raw, filename):
    return extract_pcap(raw) if filename.lower().endswith((".pcap", ".pcapng")) else extract_csv(raw)
