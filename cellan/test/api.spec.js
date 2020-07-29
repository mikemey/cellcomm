/* global describe it before after */
const TestServer = require('./testServer')

describe('Cellan API', () => {
  const server = new TestServer()

  const path = server.cfg.serverPath

  const requestEncoding = encId => server.request().get(`${path}/api/encoding/${encId}`)
  const requestIteration = (encId, it) => server.request().get(`${path}/api/encit/${encId}/${it}`)
  const requestCell = (dataId, cid) => server.request().get(`${path}/api/cell/${dataId}/${cid}`)

  const testEncodings = [
    { _id: 'VLR5000', date: null, defit: 8009, src: 'GSE122930_Sham_1_week' },
    { _id: 'TESTRUN', date: null, defit: 29, src: 'GSE122930_Sham_4_weeks_repA+B' },
    { _id: 'LR9990', date: null, defit: 1412, src: 'GSE122930_Sham_4_week' }
  ]

  const testIterations = [
    { eid: 'VLR5000', it: 5009, cids: [1, 2, 3] },
    { eid: 'VLR5000', it: 5019, cids: [1, 2, 3] },
    { eid: 'VLR5000', it: 5029, cids: [1, 2, 3] }
  ]

  const testCells = [
    { sid: 'GSE122930_Sham_1_week', cid: 1, n: 'AAACGGGTCTGATTCT-1', g: [1] },
    { sid: 'GSE122930_Sham_1_week', cid: 2, n: 'AAACGGGTCTGATTCT-2', g: [2] },
    { sid: 'GSE122930_Sham_1_week', cid: 3, n: 'AAACGGGTCTGATTCT-3', g: [3] }
  ]

  const clearDatabaseIdsFromTestData = () => {
    const removeIdField = arr => arr.forEach(el => delete el._id)
    return [testEncodings, testIterations, testCells].forEach(removeIdField)
  }

  before(() => server.start()
    .then(() => server.insertEncodings(testEncodings))
    .then(() => server.insertIterations(testIterations))
    .then(() => server.insertCells(testCells))
    .then(clearDatabaseIdsFromTestData)
  )

  after(() => server.stop())

  describe('encodings', () => {
    it('invalid encoding -> 404', () => requestEncoding('5').expect(404))

    it('valid encoding -> returns encodings', () => requestEncoding('LR9990')
      .expect(200, testEncodings[2])
    )
  })

  describe('iterations', () => {
    it('invalid encoding-id -> 404', () => requestIteration('4', 5009).expect(404))
    it('invalid iteration -> 404', () => requestIteration('VLR5000', '5').expect(404))

    it('valid iteration -> returns iterations', () => requestIteration('VLR5000', 5009)
      .expect(200, testIterations[0])
    )
  })

  describe('cells', () => {
    it('invalid cell-id -> 404', () => requestCell('GSE122930_Sham_1_week', '5').expect(404))
    it('invalid data-id -> 404', () => requestCell('5', '3').expect(404))

    it('valid cell-id -> returns cell', () => requestCell('GSE122930_Sham_1_week', '3')
      .expect(200, testCells[2])
    )
  })
})
