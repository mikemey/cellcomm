const path = require('path')
const express = require('express')
const { MongoClient } = require('mongodb')

const defaultConfig = {
  port: 13013,
  interface: '0.0.0.0',
  serverPath: '/cellan',
  defaultEncoding: 9219,
  mongodb: {
    url: 'mongodb://127.0.0.1:27017',
    dbName: 'cellcomm',
    cellsColl: 'cells',
    encodingsColl: 'encs'
  }
}

const sendFrontendFile = (res, fileName) => res.sendFile(path.join(__dirname, '..', 'frontend', fileName))

const createMainPageRouter = (encodingsColl, config) => {
  const router = express.Router()
  const defaultPath = `${config.serverPath}/${config.defaultEncoding}`

  router.get('/:enc?', (req, res) => {
    const redirectToDefault = () => res.redirect(303, defaultPath)
    return req.params.enc
      ? encodingsColl.findOne({ _id: req.params.enc })
        .then(ret => ret
          ? sendFrontendFile(res, 'index.html')
          : sendFrontendFile(res, 'error.html')
        )
      : redirectToDefault()
  })

  return router
}

const createStaticRouter = () => {
  const router = express.Router()
  router.get('/index.:ext', (req, res) => sendFrontendFile(res, `index.${req.params.ext}`))
  return router
}

const createCellRouter = cellsColl => {
  const router = express.Router()

  router.get('/cell/:id', (req, res) => {
    const cellId = req.params.id
    return cellsColl.find({ _id: cellId }).toArray()
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
      .then(db => Promise.all([
        db.collection(this.cfg.mongodb.encodingsColl),
        db.collection(this.cfg.mongodb.cellsColl)
      ]))
      .then(([encodingsColl, cellsColl]) => {
        const app = express()

        app.use(`${this.cfg.serverPath}/api`, createCellRouter(cellsColl))
        app.use(`${this.cfg.serverPath}`, createStaticRouter())
        app.use(`${this.cfg.serverPath}`, createMainPageRouter(encodingsColl, this.cfg))

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
