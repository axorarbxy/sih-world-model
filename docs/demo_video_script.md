# Two Minute Demo Script

## 0 to 15 seconds

Show the dashboard. Explain that the system forecasts the next network states from five-second traffic windows before an attack completes.

## 15 to 35 seconds

Upload `backend/data/sample_network_traffic.csv`. Explain that it represents normal traffic changing into suspicious SMB activity on port 445.

## 35 to 60 seconds

Point to the Forecast Timeline and MITRE ATT&CK Path. Explain that the World Model rolls forward five future states, then XGBoost maps each state to an ATT&CK stage.

## 60 to 80 seconds

Click a timeline point. Show Forecast Drivers and explain that attention and feature attribution identify the telemetry that influenced this point.

## 80 to 105 seconds

Show the Digital Twin. Compare Future A with no action against Future B with the mitigation. State the recommendation shown by the application. If the result says Continue monitoring, explain that the system avoids an unnecessary block when the counterfactual does not lower risk.

## 105 to 120 seconds

Show the Adaptive Threat Genome panel. Explain that it records a hashed, derived feature signature and no raw packet payload or IP address. Close by stating that the prototype supports offline enterprise and critical infrastructure deployments.
