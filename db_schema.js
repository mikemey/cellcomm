//
//  encs: {
//    _id: <enc-run-id>,
//    date: <run-date>,
//    defit: <default-iteration>,
//    srcs: {
//      matrix: <matrix-file>,
//      barcodes: <barcodes-file>,
//      genes: <genes-file>
//    }
//  }
//
//  encits: {
//    eid: <enc-run-id>,
//    it: <iteration-#>,
//    cids: [ <cell-id>, ... ],
//    ns: [ <cell-name>, ... ],
//    xs: [ <cell-x-coord>, ... ],
//    ys: [ <cell-y-coord>, ... ],
//    zs: [ <cell-z-coord>, ... ],
//    ds: [
//          [ <duplicate-coords-cell-id>, ... ],
//          ...
//        ]
//  }
//
//  cells: {
//    sid: <barcodes-file>,
//    cid: <cell-id>,
//    n: <cell-name>,
//    g: [
//      { <cell-gene>
//        e: <ensembl-name>,
//        m: <mgi-name>,
//        v: <value>
//      },
//      ...
//    ]
//  }


//const cnt = db.cells.count()
//var ix = 0
//
//
//db.cells.find().forEach(old => {
//  ix += 1
//  if (ix % 100 === 0) {
//    print(`processed ${ix}/${cnt}`)
//  }
//  db.cellcopy.insertOne({
//    sid: 'GSE122930_TAC_4_weeks_repA+B',
//    cid: parseInt(old._id),
//    n: old.n,
//    g: old.g
//  })
//})


// db.encs.insertOne({ 
//   _id: 'VLR50000',
//   date: new Date('2020-07-17T17:30:25Z'),
//   defit: 12209,
//   src: 'GSE122930_TAC_4_weeks_repA+B'
// })

// db.encs.find().forEach(old => {
//   ix += 1
//   if (ix % 100 === 0) {
//     print(`processed ${ix}/${cnt}`)
//   }
//   db.encits.insertOne({
//     eid: 'VLR50000',
//     it: parseInt(old._id),
//     cids: old.pids,
//     ns: old.ns,
//     xs: old.xs,
//     ys: old.ys,
//     zs: old.zs
//   })
// })
