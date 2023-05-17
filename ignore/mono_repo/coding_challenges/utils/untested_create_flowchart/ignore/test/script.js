#!/usr/bin/env node

import axios from 'axios'
import flowchart from 'flowchart.js'

console.log(flowchart)


function Data() {
  this.request_url = 'data/flowchart.txt'
  this.request_method = 'get'
  this.flowchart_data = null
  this.element_id = 'chart'
  this.document = null
  this.png_path = 'data/flowchart.png'
  this.saved_to_png = false
}


// const get_flowchart_data = async (method, url) => {
//   // 
//   const config = {
//     method: method,
//     url: url,
//   }
//   const response = axios(config)
//   data = response.then((response) => response.data)
//   return data
// }


// const display_flowchart = async (flowchart_data) => {
//   // 
//   const fc = flowchart.parse(flowchart_data)
//   document = fc.drawSVG('chart')
//   return document
// }


// const save_svg_as_png = async (document, png_path, element_id) => {
//   //
//   var element = document.getElementById(element_id)

//   var canvas = document.createElement('canvas')
//   canvas.width = element.clientWidth
//   canvas.height = element.clientHeight

//   const svg = new XMLSerializer().serializeToString(element)

//   // const context = canvas.getContext('2d')
//   // const v = canvg(context, svg);
//   // await v.render();

//   // let canvasBlob = await new Promise(resolve => canvas.toBlob(resolve));

//   var img = canvas.toDataURL(png_path)
//   return true
// }


// const main = async (data) => {
//   data.flowchart_data = await get_flowchart_data(
//     method=data.request_method, 
//     url=data.request_url,
//   )
//   data.document = await display_flowchart(flowchart_data=data.flowchart_data)
//   data.saved_to_png = await save_svg_as_png(
//     document=data.document, 
//     png_path=data.png_path,
//     element_id=data.element_id
//   )
//   console.log(data)
// }


// var data = new Data()
// main(data)


