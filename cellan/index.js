$(() => {
  const service = new BackendService()
  const graphDiv = $('#cell-graph').get(0)

  const points = service.getCells().map(createScatterPoints)
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
  Plotly.newPlot(graphDiv, points, layout, display)
  graphDiv.on('plotly_click', ev => showCell(ev.points[0]))
})

const createScatterPoints = point => {
  return {
    text: [`${point.name}`], x: [point.x], y: [point.y], z: [point.z],
    mode: 'markers',
    type: 'scattergl',
    hoverinfo: 'text',
    colorscale: 'Jet',
    marker: { size: 2 },
    genes: point.genes
  }
}

const showCell = cell => {
  $('#cell-id').text(cell.text)

  const genesTable = $('#cell-genes')
  const template = $('.gene').first()
  genesTable.empty()
  cell.data.genes.forEach(gene => {
    const geneRow = template.clone()
    geneRow.find('.ensemble').text(gene.ensembl)
    geneRow.find('.mgi').text(gene.mgi)
    geneRow.find('.pval').text(gene.pval)
    genesTable.append(geneRow)
  })
}

class BackendService {
  constructor () {
    this.cells = Array.from(Array(200).keys()).map(id => {
      return {
        x: Math.floor(Math.random() * 255),
        y: Math.floor(Math.random() * 255),
        z: Math.floor(Math.random() * 255),
        name: `${id}`.repeat(6),
        genes: [
          { ensembl: 'ENSMUSG00000089699', mgi: 'Gm1992', pval: id },
          { ensembl: 'ENSMUSG00000102343', mgi: 'Gm37381', pval: 4 },
          { ensembl: 'ENSMUSG00000025900', mgi: 'Rp1', pval: 1 }
        ]
      }
    })
  }
  getCells () {
    return this.cells
  }
}

