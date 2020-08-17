var theater = theaterJS({
    "minSpeed": {
      "erase": 60,
      "type": 100
    },
  
    "maxSpeed": {
      "erase": 60,
      "type": 5
    }
})

theater
  .on('type:start, erase:start', function () {
    theater.getCurrentActor().$element.classList.add('actor__content--typing')
  })
  .on('type:end, erase:end', function () {
    theater.getCurrentActor().$element.classList.remove('actor__content--typing')
  })
  .on('type:start, erase:start', function () {
    if (theater.getCurrentActor().name === 'user') {
      document.body.classList.add('dark')
    } else {
      document.body.classList.remove('dark')
    }
  })

theater

  .addActor('user', { accuracy: 0.7, speed: 0.7 })
  .addActor('host', { accuracy: 0.9, speed: 0.9 })
  .addScene('host:Welcome!', 300)
  .addScene(' This is PickMeApp!', 1000)
  .addScene('user: Wow, I didn\'t expect that.', 600)
  .addScene('user: This is a gorgeous effect!', 1000)
  .addScene('host: Yeah, I know.', 700,' It\'s the power of coding.', 500)
  .addScene('user: What is this page for?', 730, ' Now I\'m curious 🤔',800 ,'Could you tell me?', 1200)
  .addScene('user:', 180)
  .addScene('host: This page was made by Mariano Ja...')
  .addScene('user: Briefly, please.', 1500)
  .addScene('host: Okay.', 700)
  .addScene('host: This page is intended to help people find others that are traveling to the same location with the goal of sharing the same car.', 400)
  .addScene('user: Interesting...', 1000, ' But why would I share my car with strangers?', 600)
  .addScene('host: There are a lot of reasons.', 600)
  .addScene('user: I\'m listening.', 700)
  .addScene('host: Because you save money.', 900)
  .addScene(-11)
  .addScene('help the environment.', 830)
  .addScene(-21)
  .addScene('meet people.', 790)
  .addScene(' Apart from that, there are some places that don\'t have transportation services.', 750)
  .addScene('host: You help and you can be helped.', 1500)
  .addScene('user: I guess you\'re right.', 600,' I will try it.')