const path = require('path')
const express = require('express')
const morgan = require('morgan')
const { MongoClient } = require('mongodb')

const createApiRouter = require('./apiRouter')
const createHtmlRouter = require('./htmlRouter')

const defaultConfig = {
  port: 13013,
  interface: '0.0.0.0',
  serverPath: '/cellan',
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

const createRequestLogger = () => {
  morgan.token('clientIP', req => req.headers['x-forwarded-for'] || req.connection.remoteAddress)
  const format = ':date[iso] [:clientIP] :res[content-length]B [:status] :method :url - :response-time[0]ms :user-agent'
  return morgan(format)
}

const createStaticRouter = () => {
  const options = { maxAge: 86400000 }
  return express.static(path.join(__dirname, '..', 'frontend-static'), options)
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
        app.set('views', path.join(__dirname, '..', '/frontend'))
        app.set('view engine', 'pug')
        app.locals.basepath = this.cfg.serverPath

        const env = process.env.NODE_ENV
        if (env && env.toUpperCase() !== 'TEST') {
          app.use(createRequestLogger())
        }
        app.use(`${this.cfg.serverPath}/api`, createApiRouter(encodingsColl, iterationsColl, cellsColl))
        app.use(`${this.cfg.serverPath}/static`, createStaticRouter())
        app.use(`${this.cfg.serverPath}`, createHtmlRouter(encodingsColl, iterationsColl, this.cfg))

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
