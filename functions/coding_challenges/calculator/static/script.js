const data = document.querySelector('#data').value

// Sidebar
const button = document.querySelector('button')

button.addEventListener('click', _ => {
  document.getElementById('sidebar').classList.toggle('collapsed')
})

console.log(data)


// Dropdown menus for sidebar
document.querySelectorAll('[data-toggle~=dropdown]').forEach(setupDropdown);

function setupDropdown(dropdownToggle) {
  dropdownToggle.setAttribute('aria-haspopup', 'true');
  dropdownToggle.setAttribute('aria-expanded', 'false');
  
  var dropdownMenu = dropdownToggle.parentNode.querySelector('.dropdown-menu');
  
  dropdownMenu.setAttribute('aria-hidden', 'true');
  
  dropdownToggle.onclick = toggleDropdown;
  
function toggleDropdown() {
  if (dropdownToggle.getAttribute('aria-expanded') === 'true') {
    dropdownToggle.setAttribute('aria-expanded', 'false');
    dropdownMenu.setAttribute('aria-hidden', 'true');
    dropdownToggle.parentNode.classList.remove('dropdown-on');
    return;
  }
  dropdownToggle.setAttribute('aria-expanded', 'true');
  dropdownMenu.setAttribute('aria-hidden', 'false');
  dropdownToggle.parentNode.classList.add('dropdown-on');
  dropdownMenu.children[0].focus();
  return;
  }
}

function toggleParentClass(elem, className) {
  elem.parentNode.classList.toggle(className);
}

function addParentClass(elem, className) {
  elem.parentNode.classList.add(className);
}

function removeParentClass(elem, className) {
  elem.parentNode.classList.remove(className);
}

function toggleMenu() {
  var elem = document.getElementById('main-nav');
  elem.classList.toggle('menu-on');
}