const express = require('express')
const moment = require('moment')

const mainPage = 'main'

const saveEncode = param => param && encodeURIComponent(param)

const createHtmlRouter = (encodingsColl, iterationsColl, config) => {
  const router = express.Router()

  const basePath = sub => `${config.serverPath}${sub}`

  router.get('/', (req, res) => encodingsColl.find({}).toArray()
    .then(encodings => res.render(mainPage, { encodings, moment, params: req.query }))
  )

  router.get('/:encId?/:it?', (req, res) => {
    const eid = saveEncode(req.params.encId)
    const queryIt = saveEncode(req.params.it)
    return encodingsColl.findOne({ _id: eid })
      .then(encRun => {
        if (!encRun) {
          return res.redirect(303, basePath(`?error=enc&eid=${eid}`))
        }
        if (!queryIt) {
          return res.redirect(303, basePath(`/${eid}/${encRun.defit}`))
        }
        const it = parseInt(queryIt)
        return iterationsColl.findOne({ eid, it })
          .then(iteration => {
            if (!iteration) {
              return res.redirect(303, `${config.serverPath}?error=it&eid=${eid}&it=${it}`)
            }
            return res.render('encits')
          })
      })
  })

  return router
}

module.exports = createHtmlRouter
