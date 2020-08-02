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
    genesColl: 'genes',
    iterationsColl: 'encits'
  }
}

const createRequestLogger = () => {
  morgan.token('clientIP', req => req.headers['x-forwarded-for'] || req.connection.remoteAddress)
  const format = ':date[iso] [:clientIP] :status :method :url - :response-time[0]ms (:res[content-length] bytes) :user-agent'
  return morgan(format)
}

const createStaticRouter = () => {
  const options = { maxAge: 86400000 }
  return express.static(path.join(__dirname, '..', 'frontend-static'), options)
}

const maintenanceRouter = (_, res) => res.render('maintenance')

const prepareCollections = cfg => db => Promise.all([
  db.collection(cfg.mongodb.encodingsColl),
  db.collection(cfg.mongodb.iterationsColl),
  db.collection(cfg.mongodb.cellsColl),
  db.collection(cfg.mongodb.genesColl)
]).then(([encs, encits, cells, genes]) => {
  const colls = { encs, encits, cells, genes }
  return Promise.all([
    encits.createIndex({ eid: 1, it: 1 }),
    cells.createIndex({ sid: 1, cid: 1 }),
    genes.createIndex({ sid: 1, e: 1 })
  ]).then(() => colls)
})

class CellanServer {
  constructor (config = defaultConfig) {
    this.cfg = config
    this.client = null
    this.server = null
    this.logger = new Logger()
  }

  start () {
    return MongoClient
      .connect(this.cfg.mongodb.url, { useNewUrlParser: true, useUnifiedTopology: true })
      .then(client => {
        this.client = client
        return client.db(this.cfg.mongodb.dbName)
      })
      .then(prepareCollections(this.cfg))
      .then(colls => {
        const app = express()
        app.set('views', path.join(__dirname, '..', '/frontend'))
        app.set('view engine', 'pug')
        app.locals.basepath = this.cfg.serverPath

        const env = (process.env.NODE_ENV && process.env.NODE_ENV.toLowerCase()) || 'prod'
        if (env === 'test') {
          this.logger.verbose = false
        } else {
          app.use(createRequestLogger())
        }

        if (env === 'maintain') {
          this.logger.log('maintenance mode')
          app.use(`${this.cfg.serverPath}*`, maintenanceRouter)
        } else {
          this.logger.log('default server mode')
          app.use(`${this.cfg.serverPath}/api`, createApiRouter(colls))
          app.use(`${this.cfg.serverPath}/static`, createStaticRouter())
          app.use(`${this.cfg.serverPath}`, createHtmlRouter(colls, this.cfg))
        }

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

class Logger {
  constructor () {
    this.verbose = true
  }

  log (...msg) {
    if (this.verbose) {
      console.log(...msg)
    }
  }
}

module.exports = CellanServer
