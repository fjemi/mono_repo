const data = document.querySelector('#data').value
const greeting = document.getElementById('greeting')
const url = window.location

let props = {
  data: JSON.parse(data),
  greeting: greeting,
}


const post_request = async (props) => {
  const body = JSON.stringify(props.data.query_params)
  props.response = await fetch(
    url, {
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
