const express = require('express')

const createApiRouter = (encodingsColl, iterationsColl, cellsColl) => {
  const router = express.Router()

  router.get('/encoding/:encId', (req, res) => {
    const encodingId = req.params.encId
    return encodingsColl.findOne({ _id: encodingId })
      .then(encData => encData
        ? res.status(200).send(encData)
        : res.status(404).end()
      )
  })

  router.get('/encit/:encId/:it', (req, res) => {
    const eid = req.params.encId
    const it = req.params.it
    return iterationsColl.findOne({ _id: { eid, it } })
      .then(cellData => cellData
        ? res.status(200).send(cellData)
        : res.status(404).end()
      )
  })

  router.get('/cell/:sid/:cid', (req, res) => {
    const sid = req.params.sid
    const cid = req.params.cid
    return cellsColl.findOne({ _id: { sid, cid } })
      .then(cellData => cellData
        ? res.status(200).send(cellData)
        : res.status(404).end()
      )
  })

  return router
}

module.exports = createApiRouter
