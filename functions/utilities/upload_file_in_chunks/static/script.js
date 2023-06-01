const debug = (data) => {
  if (true === false) {
    // based on environment
    return 
  }
  body = JSON.stringify({
    'data': data,
    'function': 'debug',
  })
  fetch('/', {
    method: 'post',
    body: body,
  })
}


const pako = window.pako


const get_props = async () => {
  const file = document.getElementById('file')
  const upload = document.getElementById('upload')
  const status = document.getElementById('status')
  
  var data = document.querySelector('#data').value
  data = JSON.parse(data)
  
  var props = {
    data: data,
    files: file,
    upload: upload,
    status: status,
    file_name: '',
    store: {},
  }
  return props
}


const GET_FILE_MAPPER = {
  text: 'readAsText',
  data_url: 'readAsDataURL',
  array_buffer: 'readAsArrayBuffer',
}


const read_file = async (props) => {
  file = props.files[props.i]
  return new Promise((resolve, reject) => {
    var reader = new FileReader()
    reader.onload = () => {
      resolve(reader.result)
    }
    reader.onerror = reject
    method = GET_FILE_MAPPER[props.data.query_params.read_as]
    reader[method](file)
  })
}


// process files types. contents of list files are loaded 
// and processed as strings, while others are read in as files
const EXTENSIONS = {
  // csv: load_csv,
  // json: load_json,
  // txt: null,
  // yaml: null,
  // yml: null,
  // '*': read_file,
}


const deflate_file = async (props) => {
  const file = props.store[props.file_name]
  
  let deflator = new pako.Deflate({
    level: props.data.query_params.level || 7,
    gzip: props.data.query_params.gzip || false,
  })
  deflator.push(file, true)
  output = deflator.result
  props.store[props.file_name] = output
  return props
}


const chunk_deflated_file  = async (props) => {
  const deflated_file = props.store[props.file_name]
  
  var chunks_n = deflated_file.length  
  chunks_n = chunks_n / (props.data.query_params.chunk_size_kb * 1024)
  chunks_n = Math.ceil(chunks_n)
  
  let chunks = []
  
  var a = 0
  for (let i = 0; i < chunks_n; i++) {
    var b = (i + 1) * props.data.query_params.chunk_size_kb 
    b = Math.ceil(b * 1024 + 1)
    chunk = deflated_file.subarray(a, b)
    chunks.push(chunk)
    a = b
  }
  props.store[props.file_name] = chunks
  return props
}


const send_chunks_as_form_data = async (props) => {
  const chunks = props.store[props.file_name]
  let responses = []

  for (let i = 0; i < chunks.length; i++) {
    var chunk = chunks[i]
    var json = {
      file_name: props.file_name,
      chunks_n: chunks.length,
      chunk_i: i,
      location: props.data.query_params.location,
      read_as: props.data.query_params.read_as,
    }
    json = JSON.stringify(json)
    let binary = new Blob([chunk.buffer])
    const form_data = new FormData()
    
    form_data.append('binary', binary)
    console.log(chunk.buffer, chunk)
    form_data.append('json', json)
    
    const function_path = props.data.path_params.function_path
    let response = await fetch(`/${function_path}`, {
      method: 'post',
      body: form_data,
    })
    responses.push(response.ok)
  }
  props.store[props.file_name] = responses
  return props
}


const main = async () => {
  var props = await get_props()
  props.status.innerHTML = 'Uploading...'
  props.files = props.files.files
  for (let i = props.files.length - 1; i >= 0; i--) {
    props.i = i
    props.file_name = props.files[i].name
    props.store[props.file_name] = await read_file(props=props)
    props.files[i] = null
    props = await deflate_file(props=props)
    props = await chunk_deflated_file(props=props)
    props = await send_chunks_as_form_data(props=props)
  }
  props.status.innerHTML = 'Upload Complete'
  return props.store
}


upload.addEventListener('click', async () => {
  await main()
})
