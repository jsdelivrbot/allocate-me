Dropzone.options.allocateDropzone = {
  init: function() {
    this.on("addedfile", function(file) {
      // Set a default thumbnail.
      this.emit("thumbnail", file, "https://www.monash.edu/__data/assets/image/0020/13718/favicon-120.png");
    });

    this.on("success", function(file, response) {
      var fileName = file.name.split('.')[0] + ".ics"
      var file = new File([response], fileName, {type: "text/calendar;charset=utf-8"});
      saveAs(file);
    });
  }
};
