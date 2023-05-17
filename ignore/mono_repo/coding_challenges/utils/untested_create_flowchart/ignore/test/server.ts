const express = require('express')


const app = express()
const web = '/web'
const port = 3000


app.use(express.static(__dirname + web))


app.listen(port, () => {
  console.log(`server started at http://localhost:${ port }`)
})
