import bgImg from "../../assets/banner.avif";

const CarouselSlide = ({title, sub, image}) => {
    return (
        <section
            className="w-full h-[650px] bg-cover bg-center px-4 md:px-8 flex items-center justify-center"
            style={{ backgroundImage: `url(${bgImg})` }}
        >
            <div className="max-w-6xl w-full flex flex-col md:flex-row items-center justify-between bg-white/90 backdrop-blur-sm rounded-xl shadow-lg p-6 md:p-10">
                {/* Left Content */}
                <div className="w-full md:w-1/2 text-center md:text-left">
                    <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 leading-tight">
                        {title}
                    </h1>
                    <p className="text-gray-700 mt-4 mb-6 text-lg md:text-xl">
                       {sub}
                    </p>
                    <button className="btn btn-primary rounded-full px-6 py-2 text-lg shadow-lg transition-transform hover:scale-105">
                        Book Now
                    </button>
                </div>

                {/* Right Image */}
                <div className="w-full md:w-1/2 mt-8 md:mt-0 flex justify-center">
                    <img
                        src={image}
                        alt="Cleaning service"
                        className="max-w-sm w-full drop-shadow-xl rounded-lg"
                    />
                </div>
            </div>
        </section>
    );
};

export default CarouselSlide;
