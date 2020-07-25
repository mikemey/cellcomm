const CellanServer = require('./backend')

const server = new CellanServer()
server.start().then(() => {
  console.log('server started')
})
