"use client";
// import Image from "next/image";
import { useRouter } from "next/navigation";

const LinkCard = ({
  href,
  title,
  // image,
}) => {
  const router = useRouter();
  const handleClick = (event) => {
    event.preventDefault();
    router.push(`${href}?exercise=${encodeURIComponent(title)}`);
  };
  return (
    <a
      href={`${href}?exercise=${encodeURIComponent(title)}`}
      onClick={handleClick}
      className="flex items-center p-1 w-full rounded-md hover:scale-105 transition-all bg-teal-400 mb-3 max-w-3xl"
    >
      <div className="flex text-center w-full h-10">
        {/* NOTE: Removed exercise logo for now */}
        {/* <div className="w-10 h-10">
            {image && (
              <Image
                className="rounded-sm"
                alt={title}
                src={image}
                width={40}
                height={40}
              />
            )}
          </div> */}
        <h2 className="flex justify-center items-center font-semibold w-full text-black">
          {title}
        </h2>
      </div>
    </a>
  );
};

export default LinkCard;
