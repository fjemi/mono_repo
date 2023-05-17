    // var data = $('#data').data()
    // var data = 
    const data = document.getElementById('data').value
    const fc = flowchart.parse(data)
    fc.drawSVG('display')
    // document.getElementById("display").innerHTML = data