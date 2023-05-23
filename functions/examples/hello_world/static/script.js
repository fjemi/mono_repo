const data = document.querySelector('#data').value
const greeting = document.getElementById('greeting')

let props = {
  data: JSON.parse(data),
  greeting: greeting,
}


const post_request = async (props) => {
  const body = JSON.stringify(props.data.query_params)
  props.response = await fetch(
    `/${props.data.path_params.function_path}`, {
      method: 'post',
      body: body,
    }
  )
  .then((response) => { return response.json() })
  .catch((error) => { console.log(error) })
  return props
}


const update_html = async (props) => {
  props.greeting.innerHTML = props.response.data
}


const main = async (props) => {
  props = await post_request(props=props)
  update_html(props=props)
}


main(props=props)
