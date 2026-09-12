export default function ThreatGenomePanel({data}){
  if(!data)return <section><h2>Adaptive Threat Genome</h2><p>Upload traffic to derive and anchor a privacy-preserving threat signature.</p></section>
  return <section><h2>Adaptive Threat Genome · Tamper-Evident Ledger</h2><div className={data.known?'ledger hit':'ledger'}>{data.known?'KNOWN MALICIOUS SEQUENCE':'NEW THREAT SIGNATURE ANCHORED'}</div><p><b>Signature:</b> <code>{data.signature}</code></p><p><b>Ledger hash:</b> <code>{data.record_hash}</code></p><p>Only a derived flow-feature signature is anchored; no raw packet payload, source IP, or destination IP is stored.</p></section>
}
