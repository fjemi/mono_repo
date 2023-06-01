const get_props = (app) => {
  var props = app.getAttribute('props')
  props = JSON.parse(props)
  return props.functions
}


const set_operation_links = (props) => {
  store = {}
  for (const [subject, operations] of Object.entries(props)) {
    links = ''
    for (let i = 0; i < operations.length; i++) {
      link = `
        <li>
          <a href="${operations[i].route}">${operations[i].name}</a>
        </li>
      `
      links += link
    }
    store[subject] = links
  }
  return store
}


const get_dropdowns = (props) => {
  dropdowns = ''
  for (const [subject, links] of Object.entries(props)) {
    dropdown = `
      <div class="dropdown closed">
        <h4>${subject}</h4>
        <ul class="menu">
          ${links}
        </ul>
      </div>
    `
    dropdowns += dropdown
  }
  return dropdowns
}


const get_template = (dropdowns) => {
  template = `
    <html>
      <style>
      </style>
      <div class='dropdowns'>
        ${dropdowns}
      </div>
    </html>
  `
  return template
}


var main = (app) => {
  let props = get_props(app)
  props = set_operation_links(props)
  const dropdowns = get_dropdowns(props)
  const template = get_template(dropdowns)
	return template
}


var app = document.getElementById('dropdown_menu')
app.innerHTML = main(app)
