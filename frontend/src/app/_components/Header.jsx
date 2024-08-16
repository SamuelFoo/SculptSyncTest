import Image from "next/image";

const Header = () => {
  return (
    <>
      <Image
        priority
        className="rounded-full w-[96px] h-[96px]"
        alt={"GymTeam Logo"}
        src={"/header-logo.png"}
        width={96}
        height={96}
      />
      <h1 className="font-bold mt-4 mb-8 text-2xl text-teal-400">
        Select Exercise
      </h1>
    </>
  );
};

export default Header;
