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
  return getEncodings(encodingId)
    .then(encodings => {
      const graphDiv = $('#cell-graph').get(0)
      const markers = createMarkers(encodings)

      Plotly.newPlot(graphDiv, markers, layout, display)
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

const createMarkers = encodings => {
  const text = encodings.ns.map((name, ix) => `${encodings.pids[ix]}<br>${name}`)
  return [{
    ids: encodings.pids,
    text,
    x: encodings.xs,
    y: encodings.ys,
    mode: 'markers',
    type: 'scattergl',
    hoverinfo: 'text',
    marker: {
      size: 4,
      color: encodings.zs,
      colorscale: 'Jet'
    }
  }]
}

const showCellDetails = point => getCell(point.data.ids[point.pointIndex])
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

// const getEncodings = id => $.get(`api/encoding/${id}`)
// const getCell = id => $.get(`api/cell/${id}`)

const template = Array(255)
const testPointIds = Array.from(template.keys()).map(id => id)
const testNames = Array.from(template.keys()).map(id => `${id}`.repeat(6))
const testCoords = Array.from(template.keys())

const testCells = Array.from(template.keys()).map(id => {
  return {
    _id: id,
    n: `${id}`.repeat(6),
    g: [
      { e: 'ENSMUSG00000089699', m: 'Gm1992', v: id },
      { e: 'ENSMUSG00000102343', m: 'Gm37381', v: 4 },
      { e: 'ENSMUSG00000025900', m: 'Rp1', v: 1 }
    ]
  }
})

const getEncodings = id => {
  console.log('loading encodings:', id)
  return Promise.resolve({ _id: id, pids: testPointIds, ns: testNames, xs: testCoords, ys: testCoords, zs: testCoords })
}
const getCell = id => {
  console.log('loading cell:', id)
  return Promise.resolve(testCells.find(cell => cell._id === id))
}
