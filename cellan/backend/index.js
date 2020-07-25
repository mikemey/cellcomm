const express = require('express')
const { MongoClient } = require('mongodb')

const config = {
  port: 13013,
  interface: '0.0.0.0',
  serverPath: '/cellan',
  staticOptions: { maxAge: 86400000 },
  mongodb: {
    url: 'mongodb://127.0.0.1:27017',
    dbName: 'cellcomm',
    cellColl: 'cells'
  }
}

const createCellRouter = cellCollection => {
  const router = express.Router()

  router.get('/cell/:id', (req, res) => {
    const cellId = req.params.id
    return cellCollection.find({ _id: cellId }).toArray()
      .then(cellData => res.status(200).send(cellData))
  })

  return router
}

MongoClient.connect(config.mongodb.url, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(client => client.db(config.mongodb.dbName))
  .then(db => db.collection(config.mongodb.cellColl))
  .then(cellCollection => {
    const app = express()
    app.use(`${config.serverPath}`, express.static('frontend/', config.staticOptions))
    app.use(`${config.serverPath}/api`, createCellRouter(cellCollection))

    app.listen(config.port, config.interface, () => {
      console.log('server started')
    })
  })
