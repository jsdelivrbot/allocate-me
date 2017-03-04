import Dropzone from 'dropzone'
import FileSaver from 'file-saver'

// CSS
import 'app.css'
import 'dropzone/dist/dropzone.css'
import 'normalize.css'

import fileIcon from 'file-icon.png';

Dropzone.options.allocateDropzone = {
  init() {
    this.on('addedfile', (inputFile) => {
      // Set a default thumbnail.
      this.emit('thumbnail', inputFile, fileIcon);
    })

    this.on('success', (inputFile, response) => {
      let outputFileName = inputFile.name.split('.')[0] + '.ics'
      let outputFile = new File([response], outputFileName, {type: 'text/calendar;charset=utf-8'})
      FileSaver.saveAs(outputFile)
    })
  }
}
