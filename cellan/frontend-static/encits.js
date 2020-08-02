/* global $ Plotly location history */

const transparentColor = 'rgba(0,0,0,0)'
const layout = {
  showlegend: false,
  margin: { t: 0, l: 25, b: 25, r: 0 },
  hovermode: 'closest',
  plot_bgcolor: transparentColor,
  paper_bgcolor: transparentColor,
  modebar: {
    color: 'darkgray',
    activecolor: 'black',
    bgcolor: transparentColor
  },
  xaxis: { range: [0, 255] },
  yaxis: { range: [0, 255] }
}
const display = {
  displayModeBar: true,
  modeBarButtonsToRemove: ['resetScale2d', 'select2d', 'lasso2d', 'toggleSpikelines', 'hoverClosestCartesian', 'hoverCompareCartesian'],
  displaylogo: false
}

const page = {
  basePath: null,
  encodingId: 0,
  encoding: null,
  iteration: 0,
  duplicatesLookup: null,
  cell: null,
  threshold: 0
}

const getDuplicateEntry = cellId => page.duplicatesLookup.find(d => d.cid === cellId)

$(() => {
  setPageDataFromUrl()
  addLoadListeners()
  loadIterationsSelect()
  updatePlot()
  $(window).on('popstate', () => {
    setPageDataFromUrl()
    updatePlot()
  })
})

const addLoadListeners = () => {
  $('#threshold').change(() => {
    updatePageThreshold()
    updateCellDetails()
  })
  const dupCellsSelect = $('#duplicate-cell-ids')
  dupCellsSelect.change(() => {
    const cellId = dupCellsSelect.find(':selected').val()
    return loadCellDetails(cellId)
  })
  updatePageThreshold()
}

const updatePageThreshold = () => { page.threshold = parseInt($('#threshold').val()) }

const setPageDataFromUrl = () => {
  const segments = $(location).attr('href').split('/')
  page.iteration = segments.pop()
  page.encodingId = segments.pop()
  page.basePath = segments.join('/')
}

const loadIterationsSelect = () => ensureEncoding().then(() => {
  const iterationSelect = $('#iterations')
  iterationSelect.empty()
  page.encoding.showits.forEach(it => iterationSelect.append(`<option>${it}</option>`))
  iterationSelect.change(updateIteration)
  $('#iterations').val(page.iteration)
})

const updateIteration = () => {
  page.iteration = $('#iterations').find(':selected').text()
  const newLocation = $(location).attr('href').replace(/([0-9]*)$/, page.iteration)
  history.pushState(null, '', newLocation)
  updatePlot()
}

const updatePlot = () => {
  showLoader()
  return getEncodingIteration(page.encodingId, page.iteration)
    .then(encIteration => {
      updateDuplicates(encIteration)
      const markers = createMarkers(encIteration)

      const graphDiv = $('#cell-graph').get(0)
      Plotly.newPlot(graphDiv, markers, layout, display)
      graphDiv.on('plotly_click', ev => {
        const point = ev.points[0]
        const cellId = point.data.ids[point.pointIndex]
        loadCellDetails(cellId)
      })
      graphDiv.on('plotly_afterplot', hideLoader)
    })
}

const updateDuplicates = encIteration => {
  page.duplicatesLookup = []
  encIteration.ds.forEach(dups => dups.forEach(dupCellId => {
    const pointIx = encIteration.cids.indexOf(dupCellId)
    const name = encIteration.ns[pointIx]
    page.duplicatesLookup.push({ cid: dupCellId, name, cids: dups })
  }))
}

const createMarkers = encIteration => {
  const text = encIteration.ns.map((name, ix) => {
    const cellId = encIteration.cids[ix]
    const dups = getDuplicateEntry(cellId)
    const countText = (dups && `&nbsp;&nbsp;&nbsp;&nbsp;(${dups.cids.length} dups)`) || ''
    return `${name}<br>${cellId}${countText}`
  })
  return [{
    ids: encIteration.cids,
    text,
    x: encIteration.xs,
    y: encIteration.ys,
    mode: 'markers',
    type: 'scattergl',
    hoverinfo: 'text',
    marker: {
      size: 4,
      color: encIteration.zs,
      colorscale: 'Jet'
    }
  }]
}

const loadCellDetails = cellId => {
  showLoader()
  return getCell(cellId)
    .then(cell => {
      page.cell = cell
      updateCellDetails()
    })
    .always(hideLoader)
}

const updateCellDetails = () => {
  if (page.cell && Number.isInteger(page.threshold)) {
    updateCellDetailsHeader()
    const genesTable = $('#cell-genes')
    const template = $('.gene-template').first()
    genesTable.empty()
    genesTable.append(page.cell.g
      .filter(gene => gene.v >= page.threshold)
      .map(gene => {
        const geneRow = template.clone()
        geneRow.find('.ensemble').text(gene.e)
        geneRow.find('.mgi').text(gene.m)
        geneRow.find('.gval').text(gene.v)
        return geneRow
      })
    )
  }
}

const updateCellDetailsHeader = () => {
  const dupsEntry = getDuplicateEntry(page.cell.cid)
  if (dupsEntry) {
    showDuplicateCells()
    const cellSelect = $('#duplicate-cell-ids')
    cellSelect.empty()
    cellSelect.append(dupsEntry.cids.map(cid => {
      const name = getDuplicateEntry(cid).name
      return `<option value="${cid}">${cellDisplayName(cid, name)}</option>`
    }))
    cellSelect.val(page.cell.cid)
  } else {
    showSingleCell()
    $('#single-cell-id').text(cellDisplayName(page.cell.cid, page.cell.n))
  }
}

const cellDisplayName = (id, name) => `${name} (#${id})`

const apiGet = sub => $.get(`${page.basePath}/api/${sub}`)

const ensureEncoding = () => page.encoding
  ? $.Deferred().resolve()
  : apiGet(`encoding/${page.encodingId}`)
    .then(encoding => { page.encoding = encoding })

const getEncodingIteration = (encId, it) => apiGet(`encit/${encId}/${it}`)
const getCell = cid => ensureEncoding()
  .then(() => apiGet(`cell/${page.encoding.srcs.barcodes}/${cid}`))

const showLoader = () => $('#loader').removeClass('d-none')
const hideLoader = () => $('#loader').addClass('d-none')

const showSingleCell = () => {
  $('#single-cell-row').removeClass('d-none')
  $('#duplicate-cells-row').addClass('d-none')
}

const showDuplicateCells = () => {
  $('#single-cell-row').addClass('d-none')
  $('#duplicate-cells-row').removeClass('d-none')
}
