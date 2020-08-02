/* global describe it before after */
const TestServer = require('./testServer')

describe('DB indices', () => {
  const server = new TestServer()

  before(() => server.start() // start + drop database
    .then(() => server.stop())
    .then(() => server.start(false))
  )

  after(() => server.stop())

  it('iterations', () => server.getCollectionIndices(server.cfg.mongodb.iterationsColl)
    .then(ixs => ixs[1].key.should.deep.equal({ eid: 1, it: 1 })))

  it('cells', () => server.getCollectionIndices(server.cfg.mongodb.cellsColl)
    .then(ixs => ixs[1].key.should.deep.equal({ sid: 1, cid: 1 })))

  it('genes', () => server.getCollectionIndices(server.cfg.mongodb.genesColl)
    .then(ixs => ixs[1].key.should.deep.equal({ sid: 1, m: 1 })))
})
