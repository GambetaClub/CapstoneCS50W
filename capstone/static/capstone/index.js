var theater = theaterJS()

theater
  .on('type:start, erase:start', function () {
    theater.getCurrentActor().$element.classList.add('actor__content--typing')
  })
  .on('type:end, erase:end', function () {
    theater.getCurrentActor().$element.classList.remove('actor__content--typing')
  })
  .on('type:start, erase:start', function () {
    if (theater.getCurrentActor().name === 'vader') {
      document.body.classList.add('dark')
    } else {
      document.body.classList.remove('dark')
    }
  })

theater
  .addActor('vader', { speed: 0.5, accuracy: 0.6 })
  .addActor('luke', { speed: 0.7 , accuracy: 0.9 })
  .addScene('luke:Welcome!', 300)
  .addScene('luke:This is PickMeApp!', 300)
  .addScene('vader: Wow, I didn\'t expect that!', 200)