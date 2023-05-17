// import axios from 'axios';
const axios = require('axios')


type Data = {
  request_url?: string
  request_method?: string
  flowchart_data?: string
  element_id?: string
  document?: string
  png_path?: string
  saved_to_png?: boolean
}


const getData = ({
  request_url,
  request_method,
  flowchart_data,
  element_id,
  document,
  png_path,
  saved_to_png,
}: Data): Data => {
  return {
    request_url,
    request_method,
    flowchart_data,
    element_id,
    document,
    png_path,
    saved_to_png,
  }
}


const get_flowchart_data = async (
  {method, url}: {method?: string, url?: string}
): Promise<string | any> => {
  // 
  const config = {
    method: method,
    url: url,
  }
  console.log(config)
  const response: any = axios(config)
  let data: string = response.then((response: any) => response.data)
  return data
}


const main = async (data: Data): Promise<void> => {
  data.flowchart_data = await get_flowchart_data({
    method: data.request_method,
    url: data.request_url,
  })
}


var data = getData({
  request_url: '/data/flowchart.txt',
  request_method: 'get',
})
main(data)