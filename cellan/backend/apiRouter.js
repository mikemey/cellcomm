const express = require('express')

const withoutIdField = { projection: { _id: 0 } }

const createApiRouter = (encodingsColl, iterationsColl, cellsColl) => {
  const router = express.Router()

  router.get('/encoding/:encId', (req, res) => {
    const encodingId = req.params.encId
    return encodingsColl.findOne({ _id: encodingId }, withoutIdField)
      .then(encData => encData
        ? res.status(200).send(encData)
        : res.status(404).end()
      )
  })

  router.get('/encit/:encId/:it', (req, res) => {
    const eid = req.params.encId
    const it = parseInt(req.params.it)
    return iterationsColl.findOne({ eid, it }, withoutIdField)
      .then(cellData => cellData
        ? res.status(200).send(cellData)
        : res.status(404).end()
      )
  })

  router.get('/cell/:sid/:cid', (req, res) => {
    const sid = req.params.sid
    const cid = parseInt(req.params.cid)
    return cellsColl.findOne({ sid, cid }, withoutIdField)
      .then(cellData => cellData
        ? res.status(200).send(cellData)
        : res.status(404).end()
      )
  })

  return router
}

module.exports = createApiRouter
