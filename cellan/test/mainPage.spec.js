/* global describe it before after */
const TestServer = require('./testServer')

describe('Main page + static resources', () => {
  const server = new TestServer()

  const path = server.cfg.serverPath

  const requestMainPage = id => server.request().get(`${path}${id}`)

  const testEncodings = [{ _id: '5009' }, { _id: '5019' }, { _id: '5029' }]

  before(() => server.start()
    .then(() => server.insertEncodings(testEncodings))
  )

  after(() => server.stop())

  describe('main page', () => {
    it('no slash -> redirect to default-page', () => requestMainPage('')
      .expect(303)
      .expect('Location', `${server.cfg.serverPath}/${server.cfg.defaultEncoding}`)
    )

    it('slash, no encoding-id -> redirect to default-page', () => requestMainPage('/')
      .expect(303)
      .expect('Location', `${server.cfg.serverPath}/${server.cfg.defaultEncoding}`)
    )

    it('invalid encoding-id -> respond with error page', () => requestMainPage('/999')
      .expect(200)
      .then(resp => {
        resp.text.should.contain('Encoding not found!')
      })
    )

    it('valid encoding-id -> respond with main page', () => requestMainPage('/5009')
      .expect(200)
      .then(resp => resp.text.should.include('id="cell-graph"'))
    )

    it('serve js-file', () => requestMainPage('/index.js')
      .expect(200)
      .then(resp => resp.text.should.include('global $ Plotly'))
    )

    it('serve css-file', () => requestMainPage('/index.css')
      .expect(200)
      .then(resp => resp.text.should.include('font-size'))
    )
  })
})
