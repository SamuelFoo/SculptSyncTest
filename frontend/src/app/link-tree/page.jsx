'use client';

import LinkCard from "../_components/LinkCard";
import Header from "../_components/Header";
import data from "../workout.json";

const LinkTree = () => {
    return <div className="flex items-center flex-col mx-auto w-full justify-center mt-16 px-8">
            <Header />
            { data.exercises.map(exercise => 
                <LinkCard 
                    key = {exercise.name}
                    href="/tracker" 
                    title={exercise.name} />)
            }
        </div>
}


export default LinkTree;