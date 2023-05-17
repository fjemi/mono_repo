const create_flowchart = () => {
  // Retrieve value of meta id
  const data = document.head.querySelector("meta[id='flowchart_data']")
    .getAttribute('value');
  // Create the flow chart
  const fc = flowchart.parse(data);
  fc.drawSVG('chart');
}

create_flowchart()