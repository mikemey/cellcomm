const path = require('path')
const express = require('express')
const morgan = require('morgan')
const { MongoClient } = require('mongodb')

const createApiRouter = require('./apiRouter')

const defaultConfig = {
  port: 13013,
  interface: '0.0.0.0',
  serverPath: '/cellan',
  defaultEncoding: 12209,
  mongodb: {
    url: 'mongodb://127.0.0.1:27017',
    dbName: 'cellcomm',
    cellsColl: 'cells',
    encodingsColl: 'encs',
    iterationsColl: 'encits'
  }
}

const ensureIndices = ([encodingsColl, iterationsColl, cellsColl]) => Promise.all([
  iterationsColl.createIndex({ eid: 1, it: 1 }),
  cellsColl.createIndex({ sid: 1, cid: 1 })
]).then(() => iterationsColl.indexes())
  .then(() => [encodingsColl, iterationsColl, cellsColl])

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

const createRequestLogger = () => {
  morgan.token('clientIP', req => req.headers['x-forwarded-for'] || req.connection.remoteAddress)
  const format = ':date[iso] [:clientIP] :res[content-length]B [:status] :method :url - :response-time[0]ms :user-agent'
  return morgan(format)
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
        db.collection(this.cfg.mongodb.iterationsColl),
        db.collection(this.cfg.mongodb.cellsColl)
      ]))
      .then(ensureIndices)
      .then(([encodingsColl, iterationsColl, cellsColl]) => {
        const app = express()

        if (process.env.NODE_ENV.toUpperCase() !== 'TEST') {
          app.use(createRequestLogger())
        }
        app.use(`${this.cfg.serverPath}/api`, createApiRouter(encodingsColl, iterationsColl, cellsColl))
        app.use(`${this.cfg.serverPath}`, createStaticRouter())
        app.use(`${this.cfg.serverPath}`, createMainPageRouter(encodingsColl, this.cfg))
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
