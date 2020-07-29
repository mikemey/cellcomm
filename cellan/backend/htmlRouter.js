const path = require('path')
const express = require('express')
const moment = require('moment')

const mainPage = 'main'

const createHtmlRouter = (encodingsColl, config) => {
  const router = express.Router()

  router.get('/', (_, res) => encodingsColl.find({}).toArray()
    .then(encodings => res.render(mainPage, { encodings, moment }))
  )

  return router
}

module.exports = createHtmlRouter
