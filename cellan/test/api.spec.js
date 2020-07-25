/* global describe it before after */
const TestServer = require('./testServer')

describe('cellan server', () => {
  const server = new TestServer()

  const path = server.cfg.serverPath

  const requestEncoding = id => server.request().get(`${path}/api/encoding/${id}`)
  const requestCell = id => server.request().get(`${path}/api/cell/${id}`)

  const testEncodings = [
    { _id: '5009', points: [{ id: 1, name: 'AAACGGGTCTGATTCT-1', x: 1, y: 1, z: 1 }] },
    { _id: '5019', points: [{ id: 1, name: 'AAACGGGTCTGATTCT-1', x: 1, y: 1, z: 1 }] },
    { _id: '5029', points: [{ id: 1, name: 'AAACGGGTCTGATTCT-1', x: 29, y: 29, z: 29 }] }
  ]

  const testCells = [
    { _id: '1', name: 'AAACGGGTCTGATTCT-1', genes: [1] },
    { _id: '2', name: 'AAACGGGTCTGATTCT-2', genes: [2] },
    { _id: '3', name: 'AAACGGGTCTGATTCT-3', genes: [3] }
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
})
