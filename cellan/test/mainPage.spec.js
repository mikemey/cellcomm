/* global describe it before after */
const TestServer = require('./testServer')

describe('Main page + static resources', () => {
  const server = new TestServer()

  const testPath = server.cfg.serverPath
  const requestPage = (sub = '/') => server.request().get(`${testPath}${sub}`)

  const testEncodings = [
    { _id: 'VLR5000', date: new Date('2020-07-29T11:19:17.855Z'), defit: 8009, src: 'GSE122930_Sham_1_week' },
    { _id: 'TESTRUN', date: new Date('2020-07-29T11:19:17.855Z'), defit: 29, src: 'GSE122930_Sham_4_weeks_repA+B' },
    { _id: 'LR9990', date: new Date('2020-07-29T11:19:17.855Z'), defit: 1412, src: 'GSE122930_Sham_4_week' }
  ]

  before(() => server.start()
    .then(() => server.insertEncodings(testEncodings))
  )

  after(() => server.stop())

  it('shows encoding runs', () => requestPage()
    .expect(200)
    .then(data => {
      const pageText = data.text
      testEncodings.forEach(expected => {
        pageText.should.include(`${expected._id}</a>`)
        pageText.should.include(`href="./${expected._id}/${expected.defit}"`)
        pageText.should.include(`${expected.src}</td>`)
        pageText.should.include('2020-07-29 11:19</td>')
      })
    })
  )

  it('serve js-file', () => requestPage('/static/encits.js')
    .expect(200)
    .then(resp => resp.text.should.include('global $ Plotly'))
  )

  it('serve css-file', () => requestPage('/static/encits.css')
    .expect(200)
    .then(resp => resp.text.should.include('font-size'))
  )
})
