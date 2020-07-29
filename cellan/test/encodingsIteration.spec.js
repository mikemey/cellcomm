/* global describe it before after */
const TestServer = require('./testServer')

describe('Encoding iteration page', () => {
  const server = new TestServer()

  const testPath = server.cfg.serverPath
  const requestEncitsPage = (encPath, itPath) => server.request().get(`${testPath}${encPath}${itPath}`)

  const testEncodings = [{ _id: 'ABC', defit: 20, src: 'test-source' }]
  const testIterations = [{ eid: 'ABC', it: 20 }, { eid: 'ABC', it: 21 }]

  before(() => server.start()
    .then(() => server.insertEncodings(testEncodings))
    .then(() => server.insertIterations(testIterations))
  )

  after(() => server.stop())

  const iterationPageInResponse = resp => resp.text.should.include('id="cell-graph"')

  it('valid enc + it: return iteration-page', () => {
    return requestEncitsPage('/ABC', '/21')
      .expect(200)
      .expect(iterationPageInResponse)
  })

  it('enc only: return default iteration-page', () => requestEncitsPage('/ABC', '')
    .expect(303)
    .expect('Location', `${testPath}/ABC/20`)
  )

  it('invalid enc: redirect to main-page', () => requestEncitsPage('/XXX', '/20')
    .expect(303)
    .expect('Location', `${testPath}?error=enc&eid=XXX`)
  )

  it('invalid it: redirect to main-page', () => requestEncitsPage('/ABC', '/22')
    .expect(303)
    .expect('Location', `${testPath}?error=it&eid=ABC&it=22`)
  )
})
