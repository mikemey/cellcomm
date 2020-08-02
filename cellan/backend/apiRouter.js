const express = require('express')

const withoutIdField = { projection: { _id: 0 } }

const createApiRouter = colls => {
  const router = express.Router()

  router.get('/encoding/:encId', (req, res) => {
    const encodingId = req.params.encId
    return colls.encs.findOne({ _id: encodingId }, withoutIdField)
      .then(encData => encData
        ? res.status(200).send(encData)
        : res.status(404).end()
      )
  })

  router.get('/encit/:encId/:it', (req, res) => {
    const eid = req.params.encId
    const it = parseInt(req.params.it)
    return colls.encits.findOne({ eid, it }, withoutIdField)
      .then(cellData => cellData
        ? res.status(200).send(cellData)
        : res.status(404).end()
      )
  })

  router.get('/cell/:sid/:cid', (req, res) => {
    const sid = req.params.sid
    const cid = parseInt(req.params.cid)
    return colls.cells.findOne({ sid, cid }, withoutIdField)
      .then(cellData => cellData
        ? res.status(200).send(cellData)
        : res.status(404).end()
      )
  })

  router.get('/gene/:sid/:mgi', (req, res) => {
    const sid = req.params.sid
    const mgi = req.params.mgi
    return colls.genes.findOne({ sid, m: mgi }, withoutIdField)
      .then(encData => encData
        ? res.status(200).send(encData)
        : res.status(404).end()
      )
  })
  return router
}

module.exports = createApiRouter
