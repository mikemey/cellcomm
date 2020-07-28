const supertest = require('supertest')

const CellanServer = require('../backend')

const testConfig = {
  port: 13014,
  interface: '127.0.0.1',
  serverPath: '/cellan-test',
  defaultEncoding: 123,
  mongodb: {
    url: 'mongodb://127.0.0.1:27017',
    dbName: 'cellcomm-test',
    cellsColl: 'cells',
    encodingsColl: 'encs',
    iterationsColl: 'encits'
  }
}

class TestServer extends CellanServer {
  constructor () {
    super(testConfig)
    this.app = null
    this.testDb = null
  }

  start (dropDatabase = true) {
    return super.start()
      .then(app => {
        this.app = app
        return this.client.db(testConfig.mongodb.dbName)
      })
      .then(db => {
        this.testDb = db
        if (dropDatabase) { return db.dropDatabase() }
      })
  }

  insertEncodings (data) {
    return this.testDb.collection(testConfig.mongodb.encodingsColl).insertMany(data)
  }

  insertIterations (data) {
    return this.testDb.collection(testConfig.mongodb.iterationsColl).insertMany(data)
  }

  insertCells (data) {
    return this.testDb.collection(testConfig.mongodb.cellsColl).insertMany(data)
  }

  request () { return supertest(this.app) }
}

module.exports = TestServer
