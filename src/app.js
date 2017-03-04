import Dropzone from 'dropzone'
import FileSaver from 'file-saver'
import style from 'app.css'
import dzStyle from 'dropzone/dist/dropzone.css'

Dropzone.options.allocateDropzone = {
  init() {
    this.on('addedfile', (inputFile) => {
      // Set a default thumbnail.
      this.emit('thumbnail', inputFile, '/static/file-icon.png');
    })

    this.on('success', (inputFile, response) => {
      let outputFileName = inputFile.name.split('.')[0] + '.ics'
      let outputFile = new File([response], outputFileName, {type: 'text/calendar;charset=utf-8'})
      FileSaver.saveAs(outputFile)
    })
  }
}