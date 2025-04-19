// Import Swiper React components
import { Swiper, SwiperSlide } from 'swiper/react';

// Import Swiper styles
import 'swiper/css';
import 'swiper/css/pagination';
import 'swiper/css/navigation';

// import required modules
import { Autoplay, Pagination, Navigation } from 'swiper/modules';
import CarouselSlide from './CarouselSlide';
import cleaning from "../../assets/cleaning.jpg";
import carpentry from "../../assets/carpentry.jpg";
import painting from "../../assets/painting.jpg";

const HeroCarousel = () => {

    const slides = [
        {
            title: "Professional House Cleaning Services",
            sub: "Reliable. Affordable. Delivered with care.",
            image: cleaning
        },
        {
            title: "Expert Carpentry Solutions",
            sub: "Custom woodwork crafted to perfection.",
            image: carpentry
        },
        {
            title: "Precision Painting Services",
            sub: "Flawless finishes that refresh your space.",
            image: painting
        }
    ];
    
  return (
    <>
      <Swiper
        centeredSlides={true}
        autoplay={{
          delay: 3000,
          disableOnInteraction: false,
        }}
        pagination={{
          clickable: true,
        }}
        navigation={true}
        modules={[Autoplay, Pagination, Navigation]}
        className="mySwiper"
      >
        {slides.map((slide, index) => (
          <SwiperSlide key={index}>
            <CarouselSlide title={slide.title} sub={slide.sub} image={slide.image} />
          </SwiperSlide>
        ))}
      </Swiper>
    </>
  );
}

export default HeroCarousel;
