/* global describe it before after */
const TestServer = require('./testServer')

describe('cellan server', () => {
  const server = new TestServer()

  const path = server.cfg.serverPath

  const requestEncoding = id => server.request().get(`${path}/api/encoding/${id}`)
  const requestCell = id => server.request().get(`${path}/api/cell/${id}`)

  const testEncodings = [
    { _id: '5009', points: [{ id: 1, n: 'AAACGGGTCTGATTCT-1', x: 1, y: 1, z: 1 }] },
    { _id: '5019', points: [{ id: 1, n: 'AAACGGGTCTGATTCT-1', x: 1, y: 1, z: 1 }] },
    { _id: '5029', points: [{ id: 1, n: 'AAACGGGTCTGATTCT-1', x: 29, y: 29, z: 29 }] }
  ]

  const testCells = [
    { _id: '1', n: 'AAACGGGTCTGATTCT-1', g: [1] },
    { _id: '2', n: 'AAACGGGTCTGATTCT-2', g: [2] },
    { _id: '3', n: 'AAACGGGTCTGATTCT-3', g: [3] }
  ]

  before(() => server.start()
    .then(() => server.insertEncodings(testEncodings))
    .then(() => server.insertCells(testCells))
  )

  after(() => server.stop())

  describe('encodings', () => {
    it('invalid encoding -> 404', () => requestEncoding('5').expect(404))

    it('valid encoding -> returns encodings', () => requestEncoding('5029')
      .expect(200, testEncodings[2])
    )
  })

  describe('cells', () => {
    it('invalid cell-id -> 404', () => requestCell('5').expect(404))

    it('valid cell-id -> returns cell', () => requestCell('3')
      .expect(200, testCells[2])
    )
  })
})
