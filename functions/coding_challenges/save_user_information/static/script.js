const form = document.forms.namedItem("user-information-form")
const status = {
  success: 'Your user information was submitted!',
  failure: 'Error CODE occurred trying to submit your information.',
}
const url = window.location.pathname


form.addEventListener(
  "submit",
  (event) => {
    const output = document.querySelector("#output")
    const formData = new FormData(form)
    console.log(formData)

    const request = new XMLHttpRequest()
    request.open("POST", url, true)
    request.onload = (progress) => {
      output.innerHTML =
        request.status === 200
          ? status.success
          : status.failure.replace('CODE', request.status)
    }

    request.send(formData)
    event.preventDefault()
  },
  false
)
