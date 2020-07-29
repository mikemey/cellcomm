/* global describe it before after */
const TestServer = require('./testServer')

describe('Maintenance page', () => {
  const server = new TestServer()

  const testPath = server.cfg.serverPath
  const requestPage = sub => server.request().get(`${testPath}${sub}`)

  let envBak
  before(() => {
    envBak = process.env.NODE_ENV
    process.env.NODE_ENV = 'MAINTAIN'
    return server.start()
  })

  after(() => {
    process.env.NODE_ENV = envBak
    return server.stop()
  })

  it('serve maintenance mode page', () => requestPage('/any')
    .expect(200)
    .then(resp => resp.text.should.include('under maintenance'))
  )
})
