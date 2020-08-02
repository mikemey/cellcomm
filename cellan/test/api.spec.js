/* global describe it before after */
const TestServer = require('./testServer')

describe('Cellan API', () => {
  const server = new TestServer()

  const path = server.cfg.serverPath

  const requestEncoding = encId => server.request().get(`${path}/api/encoding/${encId}`)
  const requestIteration = (encId, it) => server.request().get(`${path}/api/encit/${encId}/${it}`)
  const requestCell = (dataId, cid) => server.request().get(`${path}/api/cell/${dataId}/${cid}`)
  const requestGene = (dataId, geneId) => server.request().get(`${path}/api/gene/${dataId}/${geneId}`)

  const testEncodings = [
    { _id: 'VLR5000', date: null, defit: 8009, showits: [20, 30], srcs: { barcodes: 'GSE122930_Sham_1_week_barcodes.tsv' } },
    { _id: 'TESTRUN', date: null, defit: 29, showits: [20, 30], srcs: { barcodes: 'GSE122930_Sham_4_weeks_repA+B_barcodes.tsv' } },
    { _id: 'LR9990', date: null, defit: 1412, showits: [20, 30], srcs: { barcodes: 'GSE122930_Sham_4_week_barcodes.tsv' } }
  ]

  const testIterations = [
    { eid: 'VLR5000', it: 5009, cids: [1, 2, 3] },
    { eid: 'VLR5000', it: 5019, cids: [1, 2, 3] },
    { eid: 'VLR5000', it: 5029, cids: [1, 2, 3] }
  ]

  const testCells = [
    { sid: 'GSE122930_Sham_1_week_barcodes.tsv', cid: 1, n: 'AAACGGGTCTGATTCT-1', g: [1] },
    { sid: 'GSE122930_Sham_1_week_barcodes.tsv', cid: 2, n: 'AAACGGGTCTGATTCT-2', g: [2] },
    { sid: 'GSE122930_Sham_1_week_barcodes.tsv', cid: 3, n: 'AAACGGGTCTGATTCT-3', g: [3] }
  ]

  const testGenes = [
    { sid: 'GSE122930_Sham_1_week_barcodes.tsv', e: 'otherID1', m: 'S100a9', cids: [1, 3, 4] },
    { sid: 'GSE122930_Sham_1_week_barcodes.tsv', e: 'otherID2', m: 'S100a8', cids: [4] }
  ]

  const clearDatabaseIdsFromTestData = () => {
    const removeIdField = arr => arr.forEach(el => delete el._id)
    return [testEncodings, testIterations, testCells, testGenes].forEach(removeIdField)
  }

  before(() => server.start()
    .then(() => server.insertEncodings(testEncodings))
    .then(() => server.insertIterations(testIterations))
    .then(() => server.insertCells(testCells))
    .then(() => server.insertGenes(testGenes))
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
    it('invalid cell-id -> 404', () => requestCell('GSE122930_Sham_1_week_barcodes.tsv', '5').expect(404))
    it('invalid data-id -> 404', () => requestCell('5', '3').expect(404))

    it('valid cell-id -> returns cell', () => requestCell('GSE122930_Sham_1_week_barcodes.tsv', '3')
      .expect(200, testCells[2])
    )
  })

  describe('gene', () => {
    it('invalid gene-id -> 404', () => requestGene('GSE122930_Sham_1_week_barcodes.tsv', 'NotHere').expect(404))
    it('invalid data-id -> 404', () => requestGene('5', 'S100a8').expect(404))

    it('valid gene-id -> returns gene', () => requestGene('GSE122930_Sham_1_week_barcodes.tsv', 'S100a8')
      .expect(200, testGenes[1])
    )
  })
})
