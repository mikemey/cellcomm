/* global $ Plotly location */

const iterations = Array.from({ length: 450 }, (_, ix) => 5009 + ix * 100)

const layout = {
  showlegend: false,
  margin: { t: 0, l: 0, b: 0, r: 0 },
  hovermode: 'closest'
}
const display = {
  displayModeBar: true,
  modeBarButtonsToRemove: ['select2d', 'lasso2d', 'toggleSpikelines', 'hoverClosestCartesian', 'hoverCompareCartesian'],
  displaylogo: false
}

$(() => {
  const encodingId = loadIterationsSelect()

  const graphDiv = $('#cell-graph').get(0)
  return getEncoding(encodingId)
    .then(result => {
      const points = result.points.map(createScatterPoints)
      Plotly.newPlot(graphDiv, points, layout, display)
      graphDiv.on('plotly_click', ev => showCellDetails(ev.points[0]))
    })
})

const loadIterationsSelect = () => {
  $('#iterations-btn').click(() => {
    const encodingId = select.find(':selected').text()
    location.href = `${encodingId}`
  })

  const select = $('#iteration')
  select.empty()
  iterations.forEach(it => select.append(`<option>${it}</option>`))

  const encodingId = $(location).attr('href').split('/').slice(-1).pop()
  select.val(encodingId)
  return encodingId
}

const createScatterPoints = point => {
  return {
    id: point.id,
    text: [`${point.id}<br>${point.n}`],
    x: [point.x],
    y: [point.y],
    z: [point.z],
    mode: 'markers',
    type: 'scattergl',
    hoverinfo: 'text',
    colorscale: 'Jet',
    marker: { size: 2 }
  }
}

const showCellDetails = point => getCell(point.data.id)
  .then(cell => {
    $('#cell-id').text(cell.n)
    const genesTable = $('#cell-genes')
    const template = $('.gene').first()
    genesTable.empty()
    cell.g.forEach(gene => {
      const geneRow = template.clone()
      geneRow.find('.ensemble').text(gene.e)
      geneRow.find('.mgi').text(gene.m)
      geneRow.find('.pval').text(gene.v)
      genesTable.append(geneRow)
    })
  })

const getEncoding = id => $.get(`api/encoding/${id}`)
const getCell = id => $.get(`api/cell/${id}`)

// const template = Array(200)
// const testPoints = Array.from(template.keys()).map(id => {
//   return {
//     id,
//     n: `${id}`.repeat(6),
//     x: Math.floor(Math.random() * 255),
//     y: Math.floor(Math.random() * 255),
//     z: Math.floor(Math.random() * 255)
//   }
// })

// const testCells = Array.from(template.keys()).map(id => {
//   return {
//     _id: id,
//     n: `${id}`.repeat(6),
//     g: [
//       { e: 'ENSMUSG00000089699', m: 'Gm1992', v: id },
//       { e: 'ENSMUSG00000102343', m: 'Gm37381', v: 4 },
//       { e: 'ENSMUSG00000025900', m: 'Rp1', v: 1 }
//     ]
//   }
// })

// const getEncoding = id => {
//   console.log('loading encodings:', id)
//   return Promise.resolve({ _id: id, points: testPoints })
// }
// const getCell = id => {
//   console.log('loading cell:', id)
//   return Promise.resolve(testCells.find(cell => cell._id === id))
// }
