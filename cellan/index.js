const createServer = require('./backend')

createServer().then(() => {
  console.log('server started')
})
