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
      graphDiv.on('plotly_afterplot', hideLoader)
    })
})

const loadIterationsSelect = () => {
  const iterationSelect = $('#iterations')
  iterationSelect.empty()
  iterations.forEach(it => iterationSelect.append(`<option>${it}</option>`))

  const encodingId = $(location).attr('href').split('/').slice(-1).pop()
  iterationSelect.val(encodingId)

  const goButton = $('#iterations-btn')
  iterationSelect.change(() => {
    goButton.removeAttr('disabled')
  })
  goButton.attr('disabled', '')
  goButton.click(() => {
    const encodingId = iterationSelect.find(':selected').text()
    location.href = `${encodingId}`
  })
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

const showCellDetails = point => {
  showLoader()
  return getCell(point.data.ids[point.pointIndex])
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
    .always(hideLoader)
}

const getEncodings = id => $.get(`api/encoding/${id}`)
const getCell = id => $.get(`api/cell/${id}`)

const showLoader = () => $('#loader').removeClass('invisible')
const hideLoader = () => $('#loader').addClass('invisible')
