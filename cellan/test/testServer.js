const supertest = require('supertest')

const CellanServer = require('../backend')

const testConfig = {
  port: 13014,
  interface: '127.0.0.1',
  serverPath: '/cellan-test',
  mongodb: {
    url: 'mongodb://127.0.0.1:27017',
    dbName: 'cellcomm-test',
    cellsColl: 'cells',
    encodingsColl: 'encs',
    genesColl: 'genes',
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

  insertGenes (data) {
    return this.testDb.collection(testConfig.mongodb.genesColl).insertMany(data)
  }

  getCollectionIndices (name) {
    return this.testDb.collection(name).indexes()
  }

  request () { return supertest(this.app) }
}

module.exports = TestServer
