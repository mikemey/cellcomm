const express = require('express')
const { MongoClient } = require('mongodb')

const defaultConfig = {
  port: 13013,
  interface: '0.0.0.0',
  serverPath: '/cellan',
  staticOptions: { maxAge: 86400000 },
  mongodb: {
    url: 'mongodb://127.0.0.1:27017',
    dbName: 'cellcomm',
    cellsColl: 'cells'
  }
}

const createCellRouter = cellsCollection => {
  const router = express.Router()

  router.get('/cell/:id', (req, res) => {
    const cellId = req.params.id
    return cellsCollection.find({ _id: cellId }).toArray()
      .then(cellData => res.status(200).send(cellData))
  })

  return router
}

class CellanServer {
  constructor (config = defaultConfig) {
    this.cfg = config
    this.client = null
    this.server = null
  }

  start () {
    return MongoClient
      .connect(this.cfg.mongodb.url, { useNewUrlParser: true, useUnifiedTopology: true })
      .then(client => {
        this.client = client
        return client.db(this.cfg.mongodb.dbName)
      })
      .then(db => db.collection(this.cfg.mongodb.cellsColl))
      .then(cellsCollection => {
        const app = express()
        app.use(`${this.cfg.serverPath}`, express.static('frontend/', this.cfg.staticOptions))
        app.use(`${this.cfg.serverPath}/api`, createCellRouter(cellsCollection))

        this.server = app.listen(this.cfg.port, this.cfg.interface)
        return app
      })
  }

  stop () {
    return Promise.all([
      this.client.close(),
      this.server.close()
    ])
  }
}

module.exports = CellanServer
