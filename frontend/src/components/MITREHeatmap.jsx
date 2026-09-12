import Plot from 'react-plotly.js';
const stages=['Reconnaissance','Initial Access','Lateral Movement','Command & Control','Exfiltration'];
export default function MITREHeatmap({data=[]}){
  const z=stages.map(stage=>data.map(item=>item.predicted_stage===stage?1:0));
  return <section><h2>MITRE ATT&CK Path</h2><Plot data={[{z,x:data.map(x=>x.timestamp),y:stages,type:'heatmap',colorscale:[[0,'#172033'],[1,'#f59e0b']],showscale:false,hovertemplate:'%{y}<br>%{x}<extra></extra>'}]} layout={{paper_bgcolor:'transparent',plot_bgcolor:'transparent',font:{color:'#cbd5e1'},margin:{t:10,l:120,r:10,b:35}}} useResizeHandler style={{width:'100%',height:'280px'}}/></section>
}
